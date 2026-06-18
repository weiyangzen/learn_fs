# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_vga.h

### Purpose
`intel_vga.h` declares the small legacy VGA management interface for the i915 display driver. It exposes VGA byte reads, VGA plane disable, and vgaarb client lifecycle hooks.

### Important APIs, Types, And Functions
The exported functions are `intel_vga_read(struct intel_display *, u16 reg, bool mmio)`, `intel_vga_reset_io_mem(struct intel_display *)`, `intel_vga_disable(struct intel_display *)`, `intel_vga_register(struct intel_display *)`, and `intel_vga_unregister(struct intel_display *)`. This source snapshot declares `intel_vga_reset_io_mem()` even though the implementation in the listed `intel_vga.c` is not present, so consumers or other build variants must supply or drop it.

### Control Flow
Initialization code registers the VGA client and later disables the VGA plane. Runtime users can read legacy VGA registers through either MMIO or port IO depending on platform support. Driver unload unregisters from VGA arbitration.

### State, Persistence, And Dependencies
The header owns no state and depends only on `linux/types.h` and an `intel_display` forward declaration. State changes occur in the implementation via PCI config, vgaarb, VGA ports, and display MMIO.

### Integration Points
Used by display driver initialization/uninitialization, modeset setup, and CRT/VGA-related helpers. It forms the compile-time boundary between general display code and legacy VGA handling.

### Risks
The declared-but-not-implemented `intel_vga_reset_io_mem()` is a build/link risk if referenced. Callers must pass the correct `mmio` mode to `intel_vga_read()` or they may hit the wrong access path. VGA functions should be invoked during controlled modeset/init paths because they manipulate global legacy decode.

### Test Signals
Build linkage, driver probe/remove, VGA arbitration logs, and legacy register reads on pre-GEN5 versus newer platforms are the primary signals.
