# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/json_writer.h

Purpose: public interface for the streaming JSON writer.

Important APIs and types: opaque `json_writer_t`; lifecycle, pretty/reset, name, printf/string/bool/float/int/null writers, field helpers, object/array collection functions, and `jsonw_err_handler_fn` typedef.

Control flow: header only.

State and persistence: writer state is opaque and allocated by `jsonw_new`.

Dependencies and integration points: includes stdbool/stdint/stdarg/stdio and Linux compiler annotations for printf checking.

Risks: declares `jsonw_float` and `jsonw_float_field`, but implementation compiles those only inside `#ifdef notused`; users should prefer `jsonw_float_fmt`/`jsonw_float_field_fmt` unless build provides definitions.

Test signals: compile/link success for used writer APIs and valid JSON output from implementation.
