# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_huc.c

## Purpose

This file manages the HuC media microcontroller lifecycle and authentication state. The kernel does not provide HuC runtime services to userspace; it loads or coordinates loading of HuC firmware, authenticates it through GuC or GSC depending on platform, tracks delayed GSC/PXP load state, and reports status for getparam/debugfs.

## Important APIs, Types, And Functions

Exported functions include `intel_huc_init_early()`, `intel_huc_init()`, `intel_huc_fini()`, `intel_huc_fini_late()`, `intel_huc_sanitize()`, `intel_huc_auth()`, `intel_huc_wait_for_auth_complete()`, `intel_huc_is_authenticated()`, `intel_huc_check_status()`, `intel_huc_update_auth_status()`, notifier registration helpers, and `intel_huc_load_status()`. The delayed-load helpers use `huc->delayed_load.fence`, `hrtimer`, notifier block, and `enum intel_huc_delayed_load_status`.

## Control Flow

Early init initializes generic firmware state and a completed delayed-load fence, rejects HuC when no VCS engine exists, and selects the authentication status registers for GuC and GSC modes. `check_huc_loading_mode()` reads GSC-load fuses where applicable, validates whether the blob has GSC headers or DMA subimage offsets, and ensures DG2 MEI or newer GSCCS dependencies exist. `intel_huc_init()` allocates a GSCCS HECI packet VMA when needed, initializes the firmware object, and marks it loadable.

Authentication through GuC calls `intel_guc_auth_huc()` with the RSA GGTT offset and waits for the configured status register. Authentication through GSC calls `intel_huc_fw_auth_via_gsccs()` for two-step platforms. DG2-style GSC-loaded HuC uses a notifier and delayed fence: MEI-GSC binding moves status to waiting-on-PXP, MEI/PXP load completion should authenticate HuC, and timers fail the delayed load if the devices do not bind in time.

## State, Dependencies, Risks, And Test Signals

State persists in `huc->fw`, `status[]`, `loaded_via_gsc`, optional `heci_pkt`, and delayed-load fence/timer/notifier state. Dependencies include GuC auth, GSC/GSCCS, MEI-GSC/MEI-PXP, PXP command definitions, RPS frequency reads, runtime PM, and HuC firmware parsing. Risks include platform-mode mismatches, missing DMA subimage offsets in GSC-enabled blobs, delayed-load races on suspend/resume or notifier unbind, and long authentication under throttling. Test signals are `I915_PARAM_HUC_STATUS`, debugfs `huc_info`, HuC auth logs, DG2 GSC delayed-load behavior, MTL two-step auth, suspend/resume reloads, and media workload power/performance behavior.
