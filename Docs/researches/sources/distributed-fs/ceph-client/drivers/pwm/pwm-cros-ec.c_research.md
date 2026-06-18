# sources/distributed-fs/ceph-client/drivers/pwm/pwm-cros-ec.c

Purpose: exposes PWM outputs controlled by a ChromeOS Embedded Controller to the host kernel.

Important APIs/types/functions: `struct cros_ec_pwm_device` stores the EC pointer and whether indexes are typed. `cros_ec_pwm_set_duty()` sends `EC_CMD_PWM_SET_DUTY`; `cros_ec_pwm_get_duty()` sends `EC_CMD_PWM_GET_DUTY`; `cros_ec_dt_type_to_pwm_type()` maps DT typed indexes to EC PWM types. `cros_ec_num_pwms()` probes generic channel count by reading sequential duties. `cros_ec_pwm_apply()` and `cros_ec_pwm_get_state()` translate between PWM state and EC duty values.

Control flow: probe gets the parent EC, chooses generic or typed mode based on compatible string, determines channel count, allocates the chip, seeds each PWM's fixed period argument to `EC_PWM_MAX_DUTY`, and registers it. Apply requires that period, rejects inverted polarity, maps disabled to duty zero, and sends the EC command.

State and persistence: driver state is only EC pointer and mode. Duty and enable state live in EC firmware; host-side requested state is cached by the PWM core and readable through EC commands.

Dependencies and integration: depends on ChromeOS EC protocol structures, EC command transport, OF bindings for `google,cros-ec-pwm` and `google,cros-ec-pwm-type`, and PWM core abstractions.

Risks and test signals: generic channel enumeration treats `-EINVAL` as end-of-list and other EC errors as fatal. The EC has fixed period and no separate enable bit, so consumers expecting period changes will fail. Test signals include generic and typed bindings, invalid type index, EC command errors, zero/nonzero duty enable translation, max channel enumeration, and get-state during probe/request.
