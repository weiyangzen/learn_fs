<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi-types.h -->
## sources/distributed-fs/orangefs/src/io/bmi/bmi-types.h

Purpose: Defines public BMI scalar types, flags, option constants, and BMI-specific error values while keeping BMI separable from the rest of PVFS where possible.

Important APIs, types, and functions: Type aliases include `bmi_size_t`, `bmi_msg_tag_t`, `bmi_context_id`, `bmi_op_id_t`, `BMI_addr_t`, `bmi_error_code_t`, and `bmi_hint`. Initialization flags include `BMI_INIT_SERVER`, `BMI_TCP_BIND_SPECIFIC`, and `BMI_AUTO_REF_COUNT`. Option constants cover address lifecycle, max sizes, method address access, TCP tuning, trusted settings, unexpected size, and transport method enumeration. Buffer and op enums define send/recv and preallocated/external buffers. Declares `bmi_errno_to_pvfs()` and `bmi_status_string()`.

Control flow and state: No runtime state. Error macros encode PVFS/BMI errno-like values with high bits and a BMI-specific marker, plus non-errno BMI status values such as `BMI_ECANCEL`, `BMI_EDEVINIT`, and `BMI_ETRYAGAIN`.

Dependencies and integration points: Includes `pvfs2-internal.h`; if PVFS types are visible, `BMI_addr_t` aliases `PVFS_BMI_addr_t`, otherwise it falls back to `int64_t`. Used by public `bmi.h`, method support, and transport code.

Risks and test signals: Numeric error encodings must remain stable for callers and logs. Any new option values need coordination across `bmi.c` and method vtables. Tests should validate errno translation and status string coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi-types.h -->
