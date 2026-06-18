# sources/distributed-fs/ceph-client/arch/arm64/kernel/rsi.c

Purpose: this file initializes Realm Management Extension RSI support for ARM Confidential Compute Realms. It detects RSI availability, configures memory encryption attributes, marks RAM protected, registers ioremap behavior, and creates a dummy platform device for RSI consumers.

Important APIs and state: `config` stores `realm_config`. `prot_ns_shared` is exported and encodes the non-secure shared PTE bit derived from IPA width. `rsi_present` is an exported static key. `cc_platform_has()` reports `CC_ATTR_MEM_ENCRYPT` in Realm world. `arm64_rsi_is_protected()` checks RIPAS state for a physical range. `arm64_rsi_init()` performs early initialization. `arm64_create_dummy_rsi_dev()` registers `RSI_PDEV_NAME` at arch init time.

Control flow: initialization requires SMC conduit, a matching RSI version, successful realm config query, successful ioremap hook registration, and memory encryption ops registration. It then iterates memblock memory and calls `rsi_set_memory_range_protected_safe()` for each range, panicking if any conversion fails, and enables the static key. The ioremap hook chooses encrypted attributes for protected/trusted ranges and decrypted attributes for empty/shared ranges.

Dependencies and integration: depends on SMCCC/PSCI conduit setup, memblock, SWIOTLB/memory encryption abstractions, ARM64 ioremap protection hooks, RSI SMC wrappers, and platform bus registration.

Risks: memory protection setup is irreversible enough that failures panic early to avoid later synchronous external aborts. Range protection checks align to RSI granules and must handle overflow. Incorrect encrypted/decrypted mapping selection can break device or shared-memory access.

Test signals: Realm boot logs showing RSI version, enabled `rsi_present`, successful protected memory conversion, ioremap behavior for trusted versus shared MMIO, and platform device creation. Failures appear as early panic or SEA on memory access.
