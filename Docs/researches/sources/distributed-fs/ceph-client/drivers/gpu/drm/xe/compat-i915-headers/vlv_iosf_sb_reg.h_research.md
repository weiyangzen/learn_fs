# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/compat-i915-headers/vlv_iosf_sb_reg.h

Purpose: forwards Valleyview IOSF sideband register definitions from the i915 tree. It defines no local state or behavior. Control flow is compile-time include delegation. Dependencies are `../../i915/vlv_iosf_sb_reg.h`. Integration points are shared display code compiled under Xe that still includes VLV register names. Risks are accidental use together with the no-op IOSF accessors, and include-path drift. Test signals are build coverage and platform feature guards preventing runtime use on Xe.
