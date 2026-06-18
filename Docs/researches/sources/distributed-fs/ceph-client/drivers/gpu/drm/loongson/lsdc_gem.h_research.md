# sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_gem.h

Purpose: declares Loongson GEM creation, PRIME import, dumb-create, GEM init, and BO debugfs helpers.

Important APIs/types/functions: `lsdc_gem_object_create`, `lsdc_dumb_create`, `lsdc_gem_init`, `lsdc_show_buffer_object`, and `lsdc_prime_import_sg_table`.

Control flow: core driver plugs these into DRM driver ops and initialization; planes and debugfs consume GEM/BO state through TTM helpers.

State and persistence: header defines no state; implementation maintains GEM object list in `lsdc_device`.

Dependencies and integration points: depends on DRM GEM/file types and local device definitions.

Risks and test signals: prototype consistency is required for DRM driver callbacks. Test build and GEM ioctl behavior.
