## sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_hw.h

### Purpose
`ivpu_hw.h` defines shared ivpu hardware state, address ranges, hardware lifecycle APIs, and inline adapters over buttress/IP-specific helpers.

### Important APIs, Types, And Functions
`struct ivpu_addr_range` stores `[start,end)` ranges. `struct ivpu_hw_info` stores IRQ callbacks, runtime/global/user/shave/dma ranges, PLL data, HWS priority-band parameters, tile fuse, SKU, config, DMA address width, D0i3 timestamps, and firewall IRQ counter. The header declares hardware init/power/reset/boot/IRQ APIs and provides inline wrappers for frequency, IRQ clear, diagnostics, telemetry, idle checks, IPC TX/RX, and doorbells.

### Control Flow
Inline wrappers route generic callers to buttress or IP functions. IRQ handler pointers installed at runtime select 37xx/40xx IP and MTL/LNL buttress behavior.

### State, Persistence, And Dependencies
`ivpu_hw_info` persists for the device lifetime. State maps directly to hardware registers and firmware boot-parameter inputs. Dependencies are ivpu driver, buttress, and IP headers.

### Integration Points
The header is the generic hardware contract used by driver init, firmware, PM, IPC, MMU, debugfs, and job submission code.

### Risks
Ranges use `end` as exclusive size calculations; off-by-one misuse can expose memory outside intended VPU VA windows. Inline wrappers assume function pointers and sublayers were initialized before use.

### Test Signals
Verify range size calculations, wrapper calls after hardware init, all function-pointer selections, telemetry/frequency values, idle/wait-for-idle behavior, and doorbell/IPC access through generic APIs.
