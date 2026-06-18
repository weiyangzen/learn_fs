# sources/distributed-fs/ceph-client/fs/tests/binfmt_elf_kunit.c

## Purpose
This KUnit test validates ELF loader helper `total_mapping_size()` for PT_LOAD program headers.

## Important APIs, Types, and Functions
The suite defines `total_mapping_size_test()`, `binfmt_elf_test_cases`, and `binfmt_elf_test_suite`. It uses `KUNIT_EXPECT_EQ()` to compare computed mapping spans against expected values.

## Control Flow and State
The test builds several `struct elf_phdr` arrays: empty/no-load cases, a real-world `/bin/mount`-style program header set, and an unordered set of PT_LOAD entries. It checks that no-load inputs report zero and that normal and unordered PT_LOAD inputs produce the same total mapping size.

## Persistence, Dependencies, and Integration
This is test-only code. It depends on KUnit and on the binfmt ELF implementation being compiled into the test translation unit or otherwise making `total_mapping_size()` visible to the test configuration.

## Risks and Test Signals
The targeted risk is ELF mapping-size calculation depending on header order or counting non-loadable segments. The test signal is precise: failures indicate regressions in how the loader determines the virtual span reserved for PT_LOAD mappings.
