# sources/distributed-fs/ceph-client/tools/testing/selftests/liveupdate/luo_test_utils.h

Purpose: public interface for LUO kexec selftest utilities.

Important APIs/types/functions: defines `LUO_DEVICE`, the variadic `fail_exit()` macro using `ksft_exit_fail_msg`, prototypes for LUO device/session helpers, memfd preserve/restore helpers, state helpers, daemonization, and the `luo_test_stage1_fn`/`luo_test_stage2_fn` callback types.

Control flow: no executable control flow; it establishes the callback contract used by the simple and multi-session kexec tests.

State and persistence: exposes functions that create persistent LUO state sessions and daemonized process pinning, but holds no state itself.

Dependencies and integration points: includes `<linux/liveupdate.h>` and `../kselftest.h`; all users must be built in the kernel selftests tree with generated/uapi headers available.

Risks: `fail_exit()` always includes `strerror(errno)`, which can be misleading if called after helper code that changed errno. The header exports low-level integer return conventions where negative errno and positive FDs share the same type.

Test signals: this header shapes how callers convert errors into kselftest failures or skips.
