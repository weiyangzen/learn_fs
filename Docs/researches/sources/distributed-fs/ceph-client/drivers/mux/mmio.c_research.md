# sources/distributed-fs/ceph-client/drivers/mux/mmio.c

Purpose: platform driver for mux controllers represented by contiguous bitfields in memory-mapped or parent regmap registers. It supports compatible strings `mmio-mux` and `reg-mux`.

Important APIs and functions: `struct mux_mmio` stores one `regmap_field *` per controller and saved `hardware_states` for suspend. `mux_mmio_get()` and `mux_mmio_set()` read/write a controller bitfield. `mux_mmio_probe()` obtains a regmap from a parent syscon for `mmio-mux`, from a mapped resource for `reg-mux`, or from the parent device as fallback. It parses `mux-reg-masks` pairs of register and mask, validates contiguous masks with `GENMASK(fls(mask)-1, ffs(mask)-1)`, allocates regmap fields, computes `states = 1 << width`, parses optional `idle-states`, and registers. NOIRQ PM callbacks save and restore all bitfields.

Control flow: probe maps firmware bitfield definitions into mux-core controllers. Runtime set operations are regmap field writes. Suspend reads each current hardware field into `hardware_states`; resume writes them back before normal interrupt-time activity resumes.

State and dependencies: state is split among mux-core cached state, regmap hardware fields, and suspend snapshots. Dependencies include OF, syscon, platform resources, regmap, and PM sleep callbacks. Risks include invalid zero or non-contiguous masks, bit width overflow in `1 << bits` if unusually wide fields are described, parent regmap fallback ambiguity, and resume failure leaving hardware routing changed. Test signals include DT validation for `mux-reg-masks`, syscon and direct MMIO variants, idle-state range, suspend/resume with changed register contents, and regmap error injection.
