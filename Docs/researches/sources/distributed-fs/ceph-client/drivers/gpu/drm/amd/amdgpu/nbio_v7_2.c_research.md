# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_2.c

## Purpose
`nbio_v7_2.c` implements NBIO 7.2/7.3/7.5-style services with special register aliases for Yellow Carp-like IPs. It handles HDP remap, revision and memory-size discovery, MC access enablement, SDMA/VCN/IH doorbells through PCIe-port access, PCIe-port index/data offsets, clock/light-sleep gating, request-size setup, and reset strap clearing.

## Important APIs, Types, And Functions
Exports are `nbio_v7_2_hdp_flush_reg` and `nbio_v7_2_funcs`. Key callbacks include `get_pcie_port_index_offset()`, `get_pcie_port_data_offset()`, `update_medium_grain_light_sleep()`, `init_registers()`, `set_reg_remap()`, and IP-version-specific `get_rev_id()` / `mc_access_enable()`.

## Control Flow
The code switches on NBIO IP version for strap and FB enable registers on `7.2.1`, `7.3.0`, and `7.5.0`, and for strap clearing on `7.3.0` and `7.5.1`. Doorbell paths use `RREG32_PCIE_PORT()`/`WREG32_PCIE_PORT()` for GDC0 SDMA, VCN, and IH ranges. Light sleep uses a richer path for `7.2.1/7.3.0/7.5.0`, programming both PCIE_CNTL2 and `BIF1_PCIE_TX_POWER_CTRL_1`.

## State And Persistence
State is stored in NBIO, GDC/PCIe port, and MMIO remap registers. It is reset-scoped and not persisted.

## Dependencies And Integration Points
It depends on generated NBIO 7.2 headers, local register aliases for related IPs, KFD remap constants, and common SOC15 NBIO calls.

## Risks
The file multiplexes several IP versions with local register definitions, so adding another NBIO minor version requires careful switch updates. Doorbell callbacks ignore the instance argument for SDMA/VCN in this implementation, which is correct only for the covered layout.

## Test Signals
Signals include correct revision ID on Yellow Carp-style parts, MC access enablement, SDMA/VCN/IH doorbell progress, clock/light-sleep flag transitions, and reset behavior after strap clearing.
