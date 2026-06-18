# sources/distributed-fs/ceph-client/security/integrity/platform_certs/machine_keyring.c

Purpose: Initializes and populates the machine keyring, used for machine-owner or platform-imputed trust.

Important APIs/types/functions: `machine_keyring_init()` initializes `INTEGRITY_KEYRING_MACHINE`. `add_to_machine_keyring()` imports certificates and falls back to the platform keyring on EFI systems when machine restrictions reject a key. `imputed_trust_enabled()` checks whether platform-provided imputed keys may be trusted, using MOK trust state on UEFI.

Control flow: The device initcall creates the keyring before late certificate loading. MOK trust is lazily cached by `trust_moklist()`, which checks for `MokListTrustedRT` in the EFI MOKvar table. Non-UEFI platforms allow imputed trust by default.

State and persistence: The initialized machine keyring persists globally. `trust_moklist()` caches `initialized` and `trust_mok` booleans.

Dependencies and integration: Depends on EFI MOK table helpers, integrity cert loading, platform keyring fallback, and key permission policy.

Risks and test signals: Risks include overly broad non-UEFI trust, fallback hiding machine restriction failures, and MOK trust cache timing. Tests should cover UEFI trusted/untrusted MOK, non-UEFI behavior, cert load failures, and fallback path.
