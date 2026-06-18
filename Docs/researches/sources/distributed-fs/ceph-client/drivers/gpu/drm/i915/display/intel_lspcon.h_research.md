# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_lspcon.h

Purpose: declares the LSPCON bridge lifecycle, capability, resume, and infoframe hook interface.

Important APIs/types/functions: includes activation/probe helpers, HDR capability detection, PCON wait/resume helpers, infoframe write/read/set hooks, and enabled-infoframe query helpers.

Control flow: digital port setup uses init and hook functions; resume paths call `intel_lspcon_resume()`; HDMI state verification can query enabled infoframes.

State and persistence behavior: implementation stores runtime bridge state in `struct intel_lspcon` embedded in `struct intel_digital_port`.

Dependencies and integration points: connects DP, HDMI, connector state, and CRTC state code to the bridge-specific implementation.

Risks: hook callers must only use infoframe operations when the bridge is active and vendor was detected.

Test signals: build coverage, hook registration on LSPCON VBT ports, and resume/capability paths.
