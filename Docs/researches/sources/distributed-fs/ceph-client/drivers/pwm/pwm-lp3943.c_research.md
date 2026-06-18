<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-lp3943.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-lp3943.c

Purpose: exposes the TI/National LP3943 LED driver’s two PWM generators as PWM providers while coordinating pin mux ownership with LP3943 GPIO/LED functions.

Important APIs/types/functions: `struct lp3943_pwm` stores the parent `lp3943` device, pin maps, period, and duty values. `lp3943_pwm_request()` maps a PWM to available LP3943 output pins parsed from `ti,pwmX` child properties. `lp3943_pwm_config()`, `lp3943_pwm_set_mode()`, `lp3943_pwm_enable()`, `lp3943_pwm_disable()`, and `lp3943_pwm_apply()` program parent regmap state.

Control flow: probe parses DT child nodes to build per-PWM pin maps, stores parent MFD data, and registers two PWMs. Request claims the mapped pins from the LP3943 mux map. Apply rejects unsupported polarity, computes LP3943 prescale/duty fields within 6.25 us to 1.6 ms period limits, writes period and duty registers, and switches mapped output pins between PWM mode and input/high-Z/disabled mode as enable changes.

State and persistence: software caches period and duty per PWM because mapping and register programming are per generator. Parent regmap registers and pin mux bits hold runtime hardware state; no system PM handling exists here.

Dependencies and integration: depends on LP3943 MFD structures, parent regmap, OF child properties, PWM core, and the shared LP3943 mux map used by sibling functions.

Risks and test signals: pin mapping conflicts are the key integration risk. Test DT parsing for `ti,pwm0`/`ti,pwm1`, request/free conflict handling, period bounds, multiple mapped pins per PWM, enable/disable mode changes, and parent MFD removal ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-lp3943.c -->
