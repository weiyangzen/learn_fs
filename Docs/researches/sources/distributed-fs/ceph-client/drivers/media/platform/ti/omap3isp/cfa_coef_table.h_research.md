# sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/cfa_coef_table.h


Purpose: Supplies static coefficient data for the OMAP3 ISP preview module’s CFA interpolation block. The file is an include fragment, not a standalone C header with guards.

Important APIs/types: Contains four brace-enclosed numeric coefficient arrays, each corresponding to a Bayer/CFA phase pattern expected by the including preview code. Values are byte-sized signed/encoded coefficients such as 244, 247, 250, 12, 27, 36, and 40 arranged in repeated filter kernels.

Control flow: There is no executable control flow. The including file inserts this initializer into a larger table and programs preview/CFA hardware from it.

State and persistence: Read-only compile-time table data. No mutable state or persistence.

Dependencies/integration: Integrated by `isppreview` code in the same driver directory. Table dimensions and order must match hardware register programming and the preview module’s Bayer pattern enumeration.

Risks and test signals: Because this is a raw initializer fragment, syntax and element count depend on the includer. Accidental reformatting or truncation can silently change image quality or overrun/underrun expected table size. Test by compiling the preview module, enabling raw Bayer preview paths, and comparing CFA output/color artifacts for all Bayer orders.
