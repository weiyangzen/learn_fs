# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/nested_dirty_log_test.c

Purpose: Tests dirty logging of nested guest memory accesses, including read faults, write faults, alias mappings, and behavior with nested TDP enabled or disabled.

Important APIs/types/functions: Defines test memslot constants, alias GPA range, `TEST_SYNC_*` stage bits, `l2_guest_code_tdp_enabled()`, `l2_guest_code_tdp_disabled()`, `l1_vmx_code()`, `l1_svm_code()`, `test_handle_ucall_sync()`, and `test_dirty_log()`. It uses dirty log bitmaps, `KVM_MEM_LOG_DIRTY_PAGES`, nested VMX/SVM helpers, and bit operations.

Control flow: The host sets up a test memory slot and alias mapping, enables dirty logging, then runs L1/L2. L2 performs reads and writes that should or should not fault depending on nested TDP mode. On each guest sync, the host checks dirty bitmaps and host memory contents, clears logs as needed, and validates that alias writes dirty the canonical page.

State and persistence behavior: Dirty bitmap state is maintained by KVM per memslot. Test pages persist in VM memory and are inspected through host virtual addresses. Nested page-table state differs by TDP mode.

Dependencies and integration points: Requires nested VMX or SVM, KVM dirty logging, guest memory aliasing, and optional nested TDP controls.

Risks and maintenance notes: Dirty logging semantics differ depending on nested TDP. The stage protocol is tight, and bitmap index calculations must match page layout exactly. Alias mapping makes false positives possible if page accounting changes.

Test signals: Passing means nested guest reads/writes trigger dirty logging and faults exactly as expected across TDP modes. Failures indicate nested MMU dirty-bit propagation or alias handling bugs.
