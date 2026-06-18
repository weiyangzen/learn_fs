# sources/distributed-fs/ceph-client/include/dt-bindings/spmi/spmi.h

Source read summary: 11 lines, 221 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/dt-bindings/spmi/spmi.h` provides the SPMI group slave ID macro used by device-tree clients that need to address grouped peripheral IDs.

Important APIs, types, and functions: The file exports 2 visible constants or packing macros; representative names are `SPMI_USID`, `SPMI_GSID`. This header does not define C functions or runtime data structures; its exported API is the set of stable macro names and numeric encodings used by DTS and drivers.

Control flow: DTS users place `SPMI_GSID` in SPMI address cells; the SPMI core and PMIC drivers interpret the encoded slave/group selector during device enumeration.

State and persistence behavior: There is no runtime persistence in this header. The values become persistent platform ABI once compiled into device trees, firmware handoff tables, or board descriptions, so compatibility depends on preserving numeric assignments.

Dependencies and integration points: It is self-contained and depends only on the device-tree C preprocessor include model.

Risks and edge cases: Because the header exports a single bus addressing token, the main risk is using it in a cell layout that expects a raw SID rather than a group SID.

Test signals: Compile SPMI DTS files and exercise PMIC child-device enumeration on platforms using grouped SPMI addressing.
