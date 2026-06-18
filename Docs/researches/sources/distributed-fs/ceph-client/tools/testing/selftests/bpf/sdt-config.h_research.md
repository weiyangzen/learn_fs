<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/sdt-config.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/sdt-config.h

## Purpose
This generated configuration header tells `sdt.h` whether the assembler supports autogrouping with `?` in `.pushsection` directives.

## Important APIs, Types, and Functions
It defines a single macro, `_SDT_ASM_SECTION_AUTOGROUP_SUPPORT`, set to `1`.

## Control Flow
There is no runtime control flow. The macro is consumed at preprocessing time by SDT macro generation.

## State and Persistence
No runtime state exists. The macro affects emitted assembly section attributes for compiled objects.

## Dependencies and Integration Points
It is included by `sdt.h`, which uses the value to choose `_SDT_ASM_AUTOGROUP`.

## Risks
If the configured value does not match assembler capabilities, generated SystemTap note sections may fail to assemble or may not group correctly with COMDAT sections.

## Test Signals
Successful compilation of code including `sdt.h` is the practical signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/sdt-config.h -->
