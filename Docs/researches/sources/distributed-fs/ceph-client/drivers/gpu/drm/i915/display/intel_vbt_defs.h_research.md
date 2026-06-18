# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_vbt_defs.h

### Purpose
`intel_vbt_defs.h` is the private packed-layout contract for parsing Intel Video BIOS Table (VBT) and BIOS Data Block (BDB) contents in `intel_bios.c`. It enumerates BDB block IDs and describes the byte-exact records for general features, child devices, display lists, panel data, backlight, power features, eDP, MIPI, compression, generic DTDs, and PRD data. The include guard deliberately rejects inclusion unless `_INTEL_BIOS_PRIVATE` is defined, keeping these firmware-facing structures local to BIOS parsing.

### Important APIs, Types, And Functions
There are no functions; the important ABI types are `struct vbt_header`, `struct bdb_header`, `enum bdb_block_id`, `struct child_device_config`, `struct bdb_general_definitions`, the LFP/eDP/MIPI/backlight/power structs, and `struct dsc_compression_parameters_entry`. Device-type, DVO-port, DP-AUX, DP-link-rate, eDP-link-rate, and DSC helper macros encode firmware values into symbolic constants. All externally consumed structures are `__packed`, and many use flexible arrays or version-annotated tail fields.

### Control Flow
Control flow lives in `intel_bios.c`; this header shapes that parser. Typical parsing reads the VBT header, follows `bdb_offset` to a BDB header, finds blocks by `enum bdb_block_id`, checks BDB version and block length, then casts byte ranges to these packed structs. Variable-size tables such as child device arrays, toggle lists, LFP pointer tables, DTD lists, and MIPI sequence data require parser-side length checks before field access.

### State, Persistence, And Dependencies
The data persists in firmware/OpRegion-provided VBT blobs and is copied into driver-owned `display->vbt` state by the parser. This header depends on Linux fixed-width integer types, bit helpers available through the driver include chain, and `intel_dsi_vbt_defs.h` for MIPI config/PPS definitions. The packed layout and version comments are the key persistence contract.

### Integration Points
`intel_bios.c` uses these definitions to discover connectors, DDC/AUX mapping, eDP link training and power sequencing, panel type, backlight method and limits, PSR/DRRS/VRR feature bits, compression capabilities, and generic timings. DSC parsing uses the compression block to seed slice and rate-control capability state consumed by `intel_vdsc.c`.

### Risks
The major risk is silent firmware-layout drift: adding or reading a field without BDB version and block-size gating can consume absent bytes or misinterpret obsolete meanings. Bitfields in packed firmware structs are compiler-layout-sensitive but established in this driver. Flexible array and zero-length array members must never be indexed without a validated count. Several constants have reused numeric IDs across BDB versions, so parser code must branch by version.

### Test Signals
Useful signals are VBT parser unit/fuzz tests with truncated blocks, old and new BDB versions, child device records of different sizes, eDP/DSC/backlight feature permutations, and real-machine boot logs confirming connector mapping, panel power sequencing, backlight ranges, and DSC capability discovery.
