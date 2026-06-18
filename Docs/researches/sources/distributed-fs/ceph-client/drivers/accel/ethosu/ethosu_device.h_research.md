# sources/distributed-fs/ceph-client/drivers/accel/ethosu/ethosu_device.h

Purpose: central Ethos-U private device header defining MMIO registers, command opcodes, bit masks, SRAM region constants, device state, and device conversion helpers.

Important APIs/types: register defines cover ID/status/command/reset/queue/base-pointer/config/protection/AXI/memory attributes for U65 and U85. `enum ethosu_cmds` lists NPU operations and configuration commands parsed by command-stream validation. `struct ethosu_device` embeds DRM device, register and SRAM mappings, gen-pool, clocks, IRQ, NPU info UAPI struct, in-flight job pointer, locks, DRM scheduler, fence context, and sequence number. `ethosu_is_u65()` derives architecture generation from the ID register.

Control flow: driver probe fills `ethosu_device`; GEM validation uses opcode constants; job submission programs base-pointer and queue registers; reset/config code writes register constants.

State and persistence: all fields are runtime device state. NPU info is cached from registers and exposed via query ioctl.

Dependencies: DRM device/scheduler, `drm/ethosu_accel.h`, Linux bitfield/bits, gen_pool, clock declarations.

Risks: register/opcode definitions are hardware ABI. U65/U85 overlapping register offsets require generation checks before writes. Region 2 is reserved for SRAM when present.

Test signals: register ID/config decode, U65 vs U85 reset configuration, command-stream validation for all opcodes used by Vela, SRAM-present and absent platforms, and job register programming.
