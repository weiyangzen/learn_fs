# sources/distributed-fs/ceph-client/drivers/platform/x86/amd/Makefile

Purpose: this Makefile maps AMD platform-x86 Kconfig symbols to built objects and subdirectories.

Important APIs, types, and functions: object rules include `obj-$(CONFIG_AMD_3D_VCACHE) += amd_3d_vcache.o` with `amd_3d_vcache-y := x3d_vcache.o`, `obj-$(CONFIG_AMD_PMC) += pmc/`, `obj-$(CONFIG_AMD_HSMP) += hsmp/`, `obj-$(CONFIG_AMD_PMF) += pmf/`, `obj-$(CONFIG_AMD_WBRF) += wbrf.o`, `obj-$(CONFIG_AMD_ISP_PLATFORM) += amd_isp4.o`, and `obj-$(CONFIG_AMD_HFI) += hfi/`.

Control flow: kbuild descends into subdirectories or links single objects based on enabled config symbols. There is no runtime control flow.

State and persistence: build artifacts are generated according to `.config`; no runtime state exists.

Dependencies and integration points: this file integrates top-level AMD symbols with implementation directories. It is tightly coupled to the Kconfig definitions in the same folder and subfolders.

Risks: mismatched object names or missing subdirectory rules would silently drop drivers from builds. Composite object naming for `amd_3d_vcache` must match module expectations.

Test signals: kernel build logs, presence of expected `.o` or `.ko` artifacts, and `modinfo` module naming validate the mapping.
