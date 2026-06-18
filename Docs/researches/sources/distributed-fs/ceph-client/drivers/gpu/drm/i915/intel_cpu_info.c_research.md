# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_cpu_info.c

Purpose: isolates CPU-family matching used by i915 workarounds so x86 family names do not collide with i915 platform names.

Important APIs/functions: `intel_match_g8_cpu()` checks the running CPU against `g8_cpu_ids`, covering Alder Lake, Comet Lake, Kaby Lake, Raptor Lake, and Rocket Lake families when `CONFIG_X86` is enabled. Non-x86 builds return false.

Control flow: on x86, the function delegates to `x86_match_cpu()` with a sentinel-terminated static match table. On other architectures, the stub avoids pulling in x86 headers.

State and persistence: stateless; it reads current CPU identity through kernel CPU matching infrastructure and stores no driver state.

Dependencies and integration: depends on `asm/cpu_device_id.h` and `asm/intel-family.h` under x86, and is consumed by workaround logic needing host CPU generation information.

Risks: incomplete CPU tables can disable a workaround on a matching system. Overmatching can enable a workaround unnecessarily. Architecture guards must remain correct for allmodconfig builds.

Test signals: x86 and non-x86 compile coverage, plus targeted workaround tests or boot logs on listed CPU families.
