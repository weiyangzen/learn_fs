# sources/distributed-fs/ceph-client/include/linux/error-injection.h

Purpose: function error-injection eligibility API.

Important APIs/types/functions: `within_error_injection_list()` and `get_injectable_error_type()`, with disabled stubs returning false/zero when `CONFIG_FUNCTION_ERROR_INJECTION` is off.

Control flow: tracing/fault-injection infrastructure checks whether a function address is injectable and what error type is legal before forcing a failure.

State/persistence: injectable function metadata is build/runtime registration state outside this header; no persistence here.

Dependencies/integration: ftrace/kprobes/error-injection infrastructure, annotated functions, and fault-injection tests.

Risks/test signals: risks are injecting into unsafe functions, wrong return type classification, or stubs masking tests when config is off. Test with annotated injectable functions, invalid addresses, config-off builds, and fault-injection selftests.
