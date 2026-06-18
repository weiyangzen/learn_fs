
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-ispif.c

## Purpose
Implements the legacy ISPIF subdevice that routes CSID outputs to VFE PIX/RDI inputs on older Qualcomm CAMSS platforms. It owns ISPIF reset, power reference counting, clock mux selection, CID/CSID/interface programming, interrupt handling, pad formats, media links, and entity registration.

## Important APIs, Types, and Functions
Exports `msm_ispif_subdev_init()`, `msm_ispif_register_entities()`, and `msm_ispif_unregister_entities()`. Key routines include `ispif_isr_8x16()`, `ispif_isr_8x96()`, `ispif_reset()`, `ispif_set_power()`, `ispif_select_clk_mux()`, `ispif_validate_intf_status()`, `ispif_wait_for_stop()`, `ispif_select_csid()`, `ispif_select_cid()`, `ispif_config_irq()`, `ispif_config_pack()`, `ispif_set_intf_cmd()`, `ispif_set_stream()`, and format/link helpers.

## Control Flow
Init chooses line count by SoC, assigns 8x16 or 8x96 format lists, maps base and clock-mux registers, requests the version-specific IRQ handler, gets clocks and reset clocks, and initializes locks/completions. Power-on resumes PM, enables clocks, resets the selected VFE side, and initializes cached interface commands. Stream-on validates a linked sink, locks config, selects the CSID clock mux, checks idle status, enables CSID/CID/IRQs/optional packed-RDI mode, and commands frame-boundary enable. Stream-off commands frame-boundary disable, waits for idle, then unwinds pack, IRQ, CID, CSID, and mux state.

## State and Persistence
`struct ispif_device` stores MMIO, clocks, reset completions, global `power_count`, command cache per VFE, locks, line array, and CAMSS pointer. `struct ispif_line` stores selected CSID, VFE id, interface, formats, pads, and subdev. State is volatile in memory and registers.

## Dependencies and Integration Points
Depends on platform resources, runtime PM, clocks, completions, mutexes, V4L2/media APIs, CSID id helpers, VFE line identity, and CAMSS power domains. It exists only for SoCs with an ISPIF block.

## Risks and Test Signals
Power reset error paths can leave one PM domain on if the second domain enable fails. `ISPIF_VFE_m_RDI_INTF_n_PACK_CFG_0_CID_c_PLAIN(c)` references `cid` rather than macro argument `c`, currently relying on local variable naming. Test reset completions, overflow ratelimited logs, link exclusivity, CSID/VFE selection, stream-on/off races, packed 10-bit RDI formats, and timeout handling.
