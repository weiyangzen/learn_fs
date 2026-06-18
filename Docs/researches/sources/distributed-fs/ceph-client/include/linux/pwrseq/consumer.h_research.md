# sources/distributed-fs/ceph-client/include/linux/pwrseq/consumer.h

Purpose: declares the consumer-side API for generic power sequencing targets.

Important APIs and types: opaque `struct pwrseq_desc` represents an acquired sequence target. APIs include `pwrseq_get()`, `pwrseq_put()`, `devm_pwrseq_get()`, `pwrseq_power_on()`, and `pwrseq_power_off()`. Disabled builds return `ERR_PTR(-ENOSYS)` or `-ENOSYS`.

Control flow: a device driver gets a sequencer descriptor for a named target, powers it on before using dependent hardware, powers it off during teardown or suspend, and releases the descriptor manually or through devm.

State and persistence: descriptor and unit state are owned by the power sequencing core/provider. Power state affects hardware rails/resets/clocks but is runtime state.

Dependencies and integration points: depends on device model, provider matching, and the power sequencing core. Integrates consumers with shared ordered power-up/down sequences.

Risks and test signals: risks include ignoring `ERR_PTR`, unbalanced on/off calls, target name mismatch, and disabled-config behavior. Test get/put lifetime, devm cleanup, shared consumers, power-on/off ordering, and no-power-sequencing builds.
