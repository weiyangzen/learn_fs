# sources/distributed-fs/ceph-client/include/dt-bindings/soc/cpm1-fsl,tsa.h

Source read summary: 14 lines, 342 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/dt-bindings/soc/cpm1-fsl,tsa.h` declares device-tree constants for the Freescale PowerQUICC time-slot assigner binding, covering power domains, boot modes, protocol selectors, endpoint IDs, or firmware resource classes depending on the SoC.

Important APIs, types, and functions: The file exports 6 visible constants or packing macros; representative names are `FSL_CPM_TSA_NU`, `FSL_CPM_TSA_SCC2`, `FSL_CPM_TSA_SCC3`, `FSL_CPM_TSA_SCC4`, `FSL_CPM_TSA_SMC1`, `FSL_CPM_TSA_SMC2`. This header does not define C functions or runtime data structures; its exported API is the set of stable macro names and numeric encodings used by DTS and drivers.

Control flow: DTS and subsystem drivers include the header to keep numeric firmware or register selectors shared between board descriptions and runtime driver code.

State and persistence behavior: There is no runtime persistence in this header. The values become persistent platform ABI once compiled into device trees, firmware handoff tables, or board descriptions, so compatibility depends on preserving numeric assignments.

Dependencies and integration points: It is self-contained and depends only on the device-tree C preprocessor include model.

Risks and edge cases: The values are ABI tokens. Wrong numbering can bind a device to the wrong power domain, protocol mux, boot mode, display endpoint, or firmware TCS class without a compiler error.

Test signals: Run dtbs_check/build coverage for DTS users, compare constants with binding YAML and firmware/register documentation, and exercise the owning driver probe paths.
