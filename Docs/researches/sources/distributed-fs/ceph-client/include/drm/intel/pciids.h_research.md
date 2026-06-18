# sources/distributed-fs/ceph-client/include/drm/intel/pciids.h

Purpose: provides Intel graphics PCI ID macro lists used by i915/xe and helper modules to build device ID tables without duplicating large ID arrays.

Important APIs/types/functions: `INTEL_PCI_DEVICE`, `INTEL_VGA_DEVICE`, and `INTEL_QUANTA_VGA_DEVICE` expand IDs into PCI table initializers. Generation/family macros group IDs from i810/i815/i830/i845/i85x/i865/i915/i945/i965/G33/GM45/G45 through Pineview, Ironlake, Sandy/Ivy Bridge, Haswell, Valleyview, Broadwell, Cherryview, Skylake, Broxton, Gemini Lake, Kaby/Coffee/Comet/Whiskey/Cannon/Ice/Tiger/Rocket/Jasper/Elkhart, DG1/DG2/ATS, Alder/Raptor/Arrow/Meteor/Ponte Vecchio/Lunar/Battlemage/Panther/Wildcat/Nova/CRI and related product families.

Control flow: no runtime code. Driver PCI tables invoke family macros with an initializer macro and per-device info pointer or flags, producing compile-time arrays for device matching and module autoloading.

State and persistence: PCI IDs are stable hardware identification data. The header does not store runtime state but defines long-lived driver matching ABI within the kernel source.

Dependencies and integration: expects Linux PCI table structures and vendor constants. Integrated by i915, xe, backlight/display helpers, and any Intel graphics module needing matched device lists.

Risks and test signals: duplicate IDs, missing IDs, wrong family grouping, or wrong info pointer can bind the wrong driver path. Test via `modinfo` aliases, PCI table build coverage, probe on representative SKUs, and automated duplicate-ID scans.
