# sources/distributed-fs/ceph-client/include/linux/string_choices.h

Purpose: centralizes common boolean-to-literal string choices so diagnostics and status messages use consistent spelling and can share deduplicated string constants.

Important APIs and types: inline helpers include `str_assert_deassert()`, `str_enable_disable()`, `str_enabled_disabled()`, `str_hi_lo()`, `str_high_low()`, `str_input_output()`, `str_on_off()`, `str_read_write()`, `str_true_false()`, `str_up_down()`, and `str_yes_no()`. Each has an inverse macro such as `str_disable_enable()` or `str_no_yes()`. `str_plural(size_t num)` returns `""` for one and `"s"` otherwise.

Control flow: callers pass a boolean and receive a pointer to a static string literal. Inverse macros negate the boolean and reuse the forward helper.

State and persistence: there is no runtime state or allocation; all results point to string literals.

Dependencies and integration points: depends only on `linux/types.h`. It integrates with printk, sysfs, trace, and driver status formatting code.

Risks and test signals: risks are semantic mismatch when a subsystem's true/false sense differs from the helper name and English-only pluralization limits. Test signals are mostly compile coverage and review of log/sysfs output for expected wording.
