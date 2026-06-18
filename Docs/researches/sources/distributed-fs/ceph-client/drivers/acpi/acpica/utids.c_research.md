# sources/distributed-fs/ceph-client/drivers/acpi/acpica/utids.c

Purpose: `utids.c` evaluates standard ACPI device identification methods and converts their AML return objects into allocated PNP device ID strings/lists.

Important APIs/types/functions: `acpi_ut_execute_HID()` evaluates `_HID` and returns a `struct acpi_pnp_device_id`. `acpi_ut_execute_UID()` evaluates `_UID`. `acpi_ut_execute_CID()` evaluates `_CID` and returns a `struct acpi_pnp_device_id_list`. `acpi_ut_execute_CLS()` evaluates `_CLS` and returns a PCI class string. Converters include `acpi_ex_eisa_id_to_string()`, `acpi_ex_integer_to_string()`, and `acpi_ex_pci_cls_to_string()`.

Control flow: HID/UID evaluate integer-or-string methods, compute output string length, allocate one struct plus string area, convert or copy, and release the AML return object. CID accepts integer/string/package, validates every package element, computes combined list and string storage, then writes each ID entry and advances a string pointer. CLS expects a package, reads up to three integer elements into base/sub/prog class bytes, and formats `BBSSPP`.

State and persistence behavior: Each successful function returns newly allocated caller-owned memory. It consumes temporary method return objects and releases them before exit. No global state is changed directly, though method execution can have AML side effects.

Dependencies and integration points: It depends on `uteval.c` for method evaluation/type checking, interpreter conversion utilities, ACPICA allocation/reference deletion, and is used by device enumeration and driver matching.

Risks and test signals: Risks include package elements being NULL or wrong type, unbounded firmware string lengths, allocation-size arithmetic for CID lists, integer UID decimal length, and accepting partial `_CLS` packages. Tests should cover integer and string HID/UID/CID, package CID with mixed entries, wrong CID element types, empty CID package, CLS packages of length 0-3+, allocation failure cleanup, and returned length/list_size correctness.
