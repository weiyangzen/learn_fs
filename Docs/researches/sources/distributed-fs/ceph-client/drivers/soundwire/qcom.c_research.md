# sources/distributed-fs/ceph-client/drivers/soundwire/qcom.c

## Purpose

`qcom.c` is the Qualcomm SoundWire manager platform driver. It supports multiple hardware register layouts, initializes the controller, handles command FIFO reads/writes, auto-enumeration, interrupts, runtime PM and clock stop, master port programming, and ASoC PDM DAI registration.

## Important APIs, types, and functions

- `struct qcom_swrm_ctrl` contains the `sdw_bus`, MMIO/regmap accessors, layout table, clocks/resets, IRQs, completions, port config, stream pointers, slave status, and FIFO command ids.
- `struct qcom_swrm_data` selects defaults and register layout for compatible versions.
- Register access is abstracted through CPU MMIO helpers or AHB bridge regmap helpers for SLIMbus-parented devices.
- FIFO helpers `qcom_swrm_cmd_fifo_wr_cmd()` and `qcom_swrm_cmd_fifo_rd_cmd()` implement `sdw_master_ops::xfer_msg`.
- IRQ handlers process slave alerts, enumeration/status changes, FIFO errors, bus clash, broadcast completion, clock-stop events, wake, and command-ignore events.
- `qcom_swrm_init()` resets/configures the controller, frame shape, auto-enumeration, interrupts, command retries, clock start, component enable, and FIFO depth.
- Master port ops are `qcom_swrm_port_params()`, `qcom_swrm_transport_params()`, and `qcom_swrm_port_enable()`.
- `qcom_swrm_compute_params()` maps configured Qualcomm port data into SoundWire transport and port parameters.
- ASoC DAI callbacks allocate/free master ports, hold runtime PM during stream use, and store/retrieve `sdw_stream_runtime` pointers.
- `qcom_swrm_probe()` is the platform probe and `swrm_runtime_suspend/resume()` handle PM.

## Control flow

Probe selects hardware data from OF match, chooses AHB bridge or MMIO register access, gets optional reset, IRQs, and interface clock, initializes locks/completions and bus ops, reads port configuration from hardware and device tree, initializes bus parameters/properties, requests main and optional wake IRQs, determines controller id, registers the SoundWire master, initializes the controller, waits briefly for auto-enumeration, registers DAIs, enables runtime PM, and creates debugfs if enabled.

Message transfer goes through command FIFO. Writes pack data/device/cmd-id/register into a FIFO command and optionally wait for broadcast completion. Reads enqueue a read command, wait for read FIFO data, verify command id, and retry with FIFO flush on mismatch. The IRQ handler loops over masked status bits until quiescent, updating slave status/enumeration and completing broadcast commands.

Stream setup is PDM-oriented. ASoC `.hw_params` allocates available Qualcomm master ports for the stream's slave runtime ports, then calls `sdw_stream_add_master()`. The common SoundWire stream layer calls `qcom_swrm_compute_params()` and port ops to program hardware transport registers and channel enable bits. `.hw_free` clears allocated port bits and removes the master runtime.

Runtime suspend waits for FIFO drain, optionally prepares and enters SoundWire clock stop, masks bus-clash interrupts, disables the interface clock, and enables wake IRQ. Runtime resume disables wake IRQ, enables the clock, either fully resets/reinitializes when clock stop is unsupported by an attached slave or restarts the bus and exits clock stop, then restores interrupts/status.

## State and persistence behavior

State includes `port_mask`, per-port `pconfig`, command ids, completions, `intr_mask`, cached `status[]`, `slave_status`, stream pointers, runtime PM state, FIFO depth, and `clock_stop_not_supported`. Hardware state persists in Qualcomm manager registers, command FIFOs, frame/port bank registers, interrupt masks, and clock/reset state. Port allocation is protected by `port_lock`; bus reconfiguration is handled by the generic SoundWire bus lock.

## Dependencies and integration points

The driver depends on OF/platform probing, regmap for AHB bridge mode, clk/reset APIs, PM runtime, wake IRQ support, ASoC DAI/component APIs, generic SoundWire bus/master/stream APIs, and Qualcomm DT properties such as `qcom,ports-offset1`, `qcom,ports-sinterval`, `qcom,din-ports`, and `qcom,dout-ports`.

## Risks and edge cases

- FIFO command-id mismatch handling is retry-based and can return `SDW_CMD_IGNORED`; noisy hardware can degrade bus transactions.
- `qcom_swrm_stream_alloc_ports()` calls `sdw_stream_add_master()` but does not check its return value, so allocation can appear successful when stream-add failed.
- `clock_stop_not_supported` is updated during enumeration based on slave `clk_stop_mode1`; multi-slave behavior depends on the last matching enumerated slave.
- Port configuration is DT-driven and version-sensitive; missing optional fields use `SWR_INVALID_PARAM`, but required fields fail probe.
- IRQ handler mutates `intr_mask` to disable recurring clash/collision/mismatch interrupts; recovery requires resume/init paths or manual reenable.
- Runtime resume resets/reinitializes the controller when clock stop is unsupported, which forces re-enumeration and can disturb active assumptions.
- The driver only advertises tested PDM-style DAIs despite broader SoundWire capabilities.

## Test signals

Validate all compatible layouts, MMIO and AHB bridge access, controller reset/init, auto-enumeration, FIFO read/write retries, broadcast completion, slave alert IRQs, bus clash masking, wake IRQ, runtime suspend/resume with and without clock stop, stream port allocation/free under multiple slaves, and DT port-configuration error cases. A focused test should assert `.hw_params` propagates `sdw_stream_add_master()` failures if fixed later.
