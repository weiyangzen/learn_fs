# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_vga.c

### Purpose
`intel_vga.c` handles legacy VGA resource ownership and disables the unused VGA plane during display initialization. It coordinates PCI VGA IO decode, bridge VGA routing, vgaarb registration, MMIO-vs-IO access paths, and the `VGACNTRL`/`CPU_VGACNTRL` state needed to prevent legacy VGA decode from interfering with KMS.

### Important APIs, Types, And Functions
Public APIs are `intel_vga_read()`, `intel_vga_disable()`, `intel_vga_register()`, and `intel_vga_unregister()`. Internal helpers select GMCH/VGA control registers, detect VGA decode, check MMIO access support, manipulate PCI command IO decode, manipulate bridge VGA control on dGPUs, and provide acquire/release wrappers around VGA legacy IO.

### Control Flow
`intel_vga_disable()` first checks GMCH-level decode and current VGA plane state. If cleanup is needed, it temporarily enables legacy IO decode or acquires vgaarb resources, turns off VGA sequencer screen output, disables VGA memory access, forces MDA decode for CGA/MDA consistency, releases resources, informs vgaarb on iGPUs, delays for hardware settling, then writes `VGA_DISP_DISABLE`. `intel_vga_set_decode()` is the vgaarb callback that enables or disables legacy VGA decode using bridge control on dGPUs or PCI IO decode on iGPUs.

### State, Persistence, And Dependencies
State persists in PCI config space, bridge control, legacy VGA registers, vgaarb bookkeeping, and display MMIO VGA control registers. Dependencies include Linux PCI, delay, vgaarb, VGA port definitions, DRM logging, `intel_de`, and `intel_vga_regs.h`.

### Integration Points
Display driver load registers with vgaarb, modeset setup disables the VGA plane, CRT load-detect paths can read VGA status via `intel_vga_read()`, and unload unregisters the VGA client. The code is especially relevant when the iGPU coexists with an external VGA-capable GPU.

### Risks
Legacy IO decode is fragile on multi-GPU systems: enabling the iGPU can steal VGA IO cycles from a current external VGA owner, while disabling IO too early can hang some reboot paths. dGPU bridge routing must not be altered incorrectly. Older platforms need `VGA_DISP_DISABLE` set even when decode is already disabled to avoid a stuck pipe. MDA/CGA decode synchronization prevents NoClaim errors after power-well resets.

### Test Signals
Useful coverage includes booting with vgacon, UEFI boots where BIOS left VGA registers dirty, hybrid iGPU+dGPU VGA arbitration, suspend/resume power-well reset, reboot/shutdown on older laptops, and register dumps showing `VGA_DISP_DISABLE` set with VGA memory decode disabled.
