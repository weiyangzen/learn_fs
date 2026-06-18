<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/sdis/sdis_2/ia_css_sdis2.host.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/sdis/sdis_2/ia_css_sdis2.host.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/sdis/sdis_2/ia_css_sdis2.host.c` is a host implementation for the AtomISP statistics-based digital image stabilization block. It is part of the Intel Camera Imaging CSS host/firmware boundary: host-side camera pipeline code uses this file to expose public CSS configuration, declare host helpers, or define the exact ISP parameter/state layout copied into the firmware binary. The source was read as a complete 340-line file for this report.

## Important APIs, Types, and Functions

functions/prototypes: `fill_row`, `ia_css_sdis2_horicoef_vmem_encode`, `ia_css_sdis2_vertcoef_vmem_encode`, `ia_css_sdis2_horiproj_encode`, `ia_css_sdis2_vertproj_encode`, `ia_css_get_isp_dvs2_coefficients`, `ia_css_sdis2_clear_coefficients`, `ia_css_get_dvs2_statistics`, `ia_css_translate_dvs2_statistics`, `ia_css_isp_dvs2_statistics_allocate`, `ia_css_isp_dvs2_statistics_free`, `ia_css_sdis2_horicoef_debug_dtrace`, `ia_css_sdis2_vertcoef_debug_dtrace`, `ia_css_sdis2_horiproj_debug_dtrace`, `ia_css_sdis2_vertproj_debug_dtrace`; default/static data: `default_sdis2_config`. These declarations and definitions are intentionally small and table-friendly so the larger CSS parameter manager can call them through generated configuration hooks.

## Control Flow

Runtime flow is host driven: pipeline setup allocates or receives CSS API configuration, calls this file's helper, and the helper fills the ISP-side parameter block used by the firmware kernel. encode helpers copy or quantize CSS-facing configuration into ISP DMEM/VMEM structures debug/dump helpers expose the host-side parameter values through `ia_css_debug_dtrace` copy/translation paths move coefficient or statistics buffers between HMM/ISP memory layouts and host arrays. The path is specific to the statistics-based digital image stabilization kernel and does not run independently of binary setup.

## State and Persistence Behavior

The code has no file-backed persistence. default `const` configuration objects are immutable process image data; statistics or coefficient payloads live in HMM/ISP memory until explicitly copied or freed. Hardware-visible persistence is limited to the ISP parameter/state memory programmed for the active AtomISP pipeline.

## Dependencies and Integration Points

Direct includes are `"hmm.h"`, `<assert_support.h>`, `"ia_css_debug.h"`, `"ia_css_sdis2.host.h"`. Important integration signals: debug tracing, binary-specific configuration dispatch, vector-memory array layout, host/ISP memory transfer, kernel assertion guards. The integration point is the AtomISP CSS parameter pipeline for statistics-based digital image stabilization: CSS API structs are translated into `sh_css_*` ISP ABI structs consumed by firmware kernels.

## Risks and Edge Cases

many helpers ignore the `size` argument, so caller/table mismatches are not locally detected; buffer copies depend on grid dimensions and caller-allocated array sizes; several paths rely on assertions for null/shape checks rather than recoverable validation.

## Test Signals

compile coverage for this AtomISP kernel and include-order coverage with the paired host/type/param headers; unit-style encoder checks that compare each source config field with the emitted ISP parameter field; debug trace smoke tests with null and populated inputs where supported; statistics/coefficient round-trip tests using representative grid dimensions and allocation failures; pipeline image-quality regression tests for the owning kernel block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/sdis/sdis_2/ia_css_sdis2.host.c -->
