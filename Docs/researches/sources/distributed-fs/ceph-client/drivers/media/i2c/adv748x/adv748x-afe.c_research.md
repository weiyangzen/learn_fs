<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/adv748x/adv748x-afe.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/adv748x/adv748x-afe.c

## Purpose
`adv748x-afe.c` implements the ADV748x analog front end and standard definition processor V4L2 subdevice. It handles analog input selection, analog TV standard setting/detection, source format reporting, controls for brightness/contrast/saturation/hue/test pattern, and stream-time power-up of the selected CSI-2 transmitter.

## Important APIs, Types, and Functions
- `struct adv748x_afe` is defined in `adv748x.h` and stores pads, controls, format, selected TX, streaming flag, current norm, and input.
- `adv748x_afe_status()` reads the SDP read-only map and translates lock/standard bits to V4L2 status and standards.
- `adv748x_afe_std()` maps V4L2 analog standards to SDP `VID_SEL` values.
- `adv748x_afe_s_input()` writes the SDP input mux.
- Video ops include `g_std`, `s_std`, `querystd`, `g_tvnorms`, `g_input_status`, and `s_stream`.
- Pad ops report a fixed `MEDIA_BUS_FMT_UYVY8_1X16` source format and propagate a fixed pixel rate to the connected CSI-2 TX.

## Control Flow
Initialization seeds NTSC-M, picks the first declared AIN endpoint as the default input, initializes one source and eight sink pads, and registers controls. Standard queries lock the global mutex, refuse to run while streaming, switch to autodetect, sleep for detection, read status, and restore the previous standard. Streaming locks the parent, optionally reselects input, powers the linked TX through `adv748x_tx_power()`, records streaming state, and logs signal lock.

## State and Persistence
`input`, `curr_norm`, `streaming`, and `tx` are in-memory state. The parent mutex serializes hardware access and control writes. No state persists across driver removal; reset scripts in core reinitialize hardware, and AFE init reapplies defaults.

## Dependencies and Integration Points
This file depends on parent register helpers/macros from `adv748x.h`, the parent `adv748x_state`, V4L2 controls/subdev APIs, media pads, and an enabled media link to a CSI-2 transmitter. It is internally registered by the CSI-2 subdevice when links are built.

## Risks
- `adv748x_afe_s_input()` accepts any unsigned input value; callers depend on endpoint parsing/defaults to avoid invalid mux values.
- Pixel-rate propagation happens during active format get and can fail with `-ENOLINK`; callers may ignore that side effect.
- Control writes first select SDP map 0, but errors from later `sdp_clrset()` chains need hardware testing.
- Streaming requires `afe->tx` to be set by media link setup; a missing link can lead to null dereference unless graph construction prevents stream calls.

## Test Signals
Test endpoint-driven default input, all AIN pads, standard set/query while idle and `-EBUSY` while streaming, input status with/without analog signal, source format height for 525/625-line modes, control writes and test-pattern selection, media links to TXA/TXB, and pixel-rate propagation to the remote CSI-2 control.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/adv748x/adv748x-afe.c -->
