
# sources/distributed-fs/ceph-client/drivers/cxl/core/atl.c

Purpose: AMD PRM-backed CXL address translation support. It installs a root operation that translates endpoint DPA/HPA ranges into system physical address ranges for normalized addressing platforms.

Important APIs, types, and functions: `prm_cxl_dpa_spa()` calls an ACPI PRM handler identified by `prm_cxl_dpa_spa_guid` with PCI segment/bus/devfn and DPA, returning SPA or `ULLONG_MAX`. `cxl_prm_setup_root()` is the `translation_setup_root` callback that validates endpoint/root assumptions, translates range endpoints, derives interleave ways/granularity, and marks decoders locked/normalized. `cxl_setup_prm_address_translation()` probes PRM support and installs the callback on a CXL root.

Control flow: ACPI root probe calls `cxl_setup_prm_address_translation()`. That verifies the host matches ACPI CXL root driver data and that the PRM handler is supported. Later, region/root setup invokes `cxl_prm_setup_root()` for endpoint decoder contexts. The callback only handles normalized addressing where HPA start equals endpoint DPA start and endpoint interleave is passthrough, translates start/end through PRM, aligns the resulting SPA range to 256 MiB, checks contiguity, probes offsets to determine interleave granularity up to 16 MiB, sets lock/normalized flags, and updates the region context.

State and persistence: no persistent local state. It updates `struct cxl_region_context` and `struct cxl_decoder` flags during setup. The PRM handler and platform firmware provide translation data.

Dependencies and integration points: depends on ACPI PRMT, PCI device identity, CXL core region/decoder structures, `cxl_memdev` endpoint relationships, and CXL root ops installed from `acpi.c`.

Risks and test signals: PRM failures return `-ENXIO` and leave translation unavailable. The granularity detection assumes probing `base + gran` reveals interleave transition behavior. The function locks decoders because the current kernel cannot reprogram normalized-addressing endpoint setups. Test signals include PRM unsupported vs supported platforms, non-PCI endpoints, non-passthrough endpoints, failed start/end translation, non-contiguous SPA ranges, multi-way/granularity derivation, and decoder flag updates.
