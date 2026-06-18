# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/pixelgen_global.h

Purpose: defines public configuration types for the CSS 2401 pixel generator, including sync generator, test-pattern generator, and PRBS modes.

Important APIs/types/functions: `isp2401_sync_generator_cfg_t` describes blanking, pixels per clock, frame count, pixels per line, and lines per frame. `pixelgen_tpg_mode_t` enumerates ramp, checkerboard, and mono modes. `pixelgen_tpg_cfg_t` contains color, mask, delta, and sync-generator settings. `pixelgen_prbs_cfg_t` contains PRBS seeds and sync-generator settings.

Control flow: no logic in the header. Pixelgen setup code converts these configs into register writes.

State and persistence: caller-owned config structures; applied hardware configuration persists until reset/reprogramming.

Dependencies and integration: depends on CSS type support and duplicates parts of broader input-system config types.

Risks and test signals: duplication from other headers can drift. Tests should verify PRBS and TPG output dimensions, color/mask/delta behavior, and sync generator frame timing.
