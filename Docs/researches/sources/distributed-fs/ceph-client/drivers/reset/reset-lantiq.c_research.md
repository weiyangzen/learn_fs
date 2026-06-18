# sources/distributed-fs/ceph-client/drivers/reset/reset-lantiq.c

Purpose: Lantiq/Intel XWAY RCU reset controller using separate reset and status offsets from a parent syscon.

Important APIs/types/functions: `struct lantiq_rcu_reset_priv`, `lantiq_rcu_reset_status()`, `lantiq_rcu_reset_status_timeout()`, `lantiq_rcu_reset_update()`, `lantiq_rcu_reset_of_parse()`, `lantiq_rcu_reset_xlate()`, and `lantiq_rcu_reset_probe()`.

Control flow: probe parses parent regmap and two address cells for reset and status offsets. Xlate accepts `(set-bit, status-bit)` and packs them into an ID. Assert/deassert update the reset bit and poll status until it matches the requested state. `.reset` asserts then deasserts.

State and persistence: hardware bits hold reset state; parsed offsets are stored in driver memory.

Dependencies and integration: OF address parsing, syscon/regmap, platform bus, reset framework.

Risks and test signals: status and set bits may differ, so DT cell order matters. Test both compatibles, missing address resources, status timeout behavior, and invalid cell rejection.
