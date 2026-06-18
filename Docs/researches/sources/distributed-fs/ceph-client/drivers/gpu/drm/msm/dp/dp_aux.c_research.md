# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dp/dp_aux.c

Purpose: Implements the MSM DP AUX adapter, including AUX/I2C-over-AUX transfers, HPD control, IRQ completion, runtime PM, EDID segment workarounds, and PHY recalibration/reset handling.

Important APIs/functions: `msm_dp_aux_get()` allocates and initializes a `drm_dp_aux` adapter with transfer and HPD wait callbacks. `msm_dp_aux_transfer()` is the DRM AUX transfer implementation. `msm_dp_aux_isr()` decodes AUX IRQ bits, records error status, clears hardware interrupts when needed, and completes waiting transfers. `msm_dp_aux_init()`/`deinit()` enable/disable AUX hardware. `msm_dp_aux_enable_xfers()` gates external DP transfers when disconnected. HPD APIs enable/disable HPD, HPD IRQs, read/ack HPD status, and report link-connected state.

Control flow: Transfer resumes the device with runtime PM, locks the AUX mutex, rejects uninitialized or disconnected external-DP transactions, tracks EDID segment/offset writes, sends helper segment/offset transactions for non-compliant sinks, programs the command FIFO, waits up to 250 ms for completion, decodes error status into DP replies or errno, and resets/recalibrates on failures. FIFO TX writes address/size/data into `REG_DP_AUX_DATA` then starts `REG_DP_AUX_TRANS_CTRL`; FIFO RX clears GO and reads indexed data bytes.

State and persistence: Private state tracks mutex/completion, last error, retry count, command busy flag, request type, no-send flags, init/connect gates, EDID offset/segment, eDP mode, PHY pointer, and MMIO base. All state is device-lifetime volatile memory.

Dependencies/integration: Depends on DRM DP AUX helpers, runtime PM, PHY API, HPD/AUX register macros, and callers in DP display/link/panel code. IRQ dispatch comes through `msm_dp_ctrl_isr()`.

Risks and test signals: `aux->native` and read detection use bitwise expressions that depend on request bit layout. EDID workaround mutates offset/segment across transactions. Unexpected IRQs when not busy are ignored. Test DPCD native reads/writes, EDID reads beyond two blocks, disconnect gating, eDP always-on AUX, timeout/reset path, HPD IRQ masking, repeated native failures triggering `phy_calibrate()`, and AUX char device access while unplugged.
