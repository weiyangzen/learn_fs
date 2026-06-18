# sources/distributed-fs/ceph-client/drivers/acpi/acpica/acconvert.h

Purpose: declares ASL/ASL+ comment conversion support for ACPICA compiler/disassembler builds.

Important APIs/macros: defines ASL comment states and AML comment print categories. Under `ACPI_ASL_COMPILER`, it declares comment capture, placement, file switching, parse-object annotation, and AML comment output functions such as `cv_process_comment`, `cv_capture_comments`, `cv_transfer_comments`, `cv_switch_files`, and `cg_write_aml_comment`.

Control flow: compiler/disassembler builds capture comments while parsing, store them on comment lists or parse objects, transfer them to the correct parse nodes, and emit them during disassembly/code generation.

State and persistence: comment state is stored in `struct asl_comment_state`, parse objects, comment lists, file nodes, and globals declared elsewhere. The header owns no storage.

Dependencies and integration: depends on parse state, walk state, parse object, table header, file, and comment-node types. `acmacros.h` maps converter hooks to real functions only when compiler support is enabled.

Risks: inactive in normal kernel builds, so drift may only show in compiler builds. Comment placement is parse-tree and include-file sensitive. Tool memory ownership for comment lists is easy to leak.

Test signals: iASL/disassembler round trips with inline, block, include, close-brace, and end-block comments; builds with and without `ACPI_ASL_COMPILER`.
