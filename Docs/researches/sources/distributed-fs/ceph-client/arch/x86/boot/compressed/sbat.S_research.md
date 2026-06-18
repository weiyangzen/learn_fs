# sources/distributed-fs/ceph-client/arch/x86/boot/compressed/sbat.S

Purpose: embeds SBAT revocation metadata into the compressed kernel image when EFI SBAT support is enabled.

Important APIs and state: this assembly has no callable API. It pushes an allocatable `.sbat` section and includes `CONFIG_EFI_SBAT_FILE` verbatim with `.incbin`.

Control flow: build-time only. The linker script collects `.sbat`, aligns it to a page, and the PE header in `header.S` advertises it as a discardable readable PE section.

Dependencies and integration: depends on Kconfig/build-system definition of `CONFIG_EFI_SBAT_FILE`, `CONFIG_EFI_SBAT`, and the compressed kernel linker script. Integration is with EFI Secure Boot revocation policy, not runtime boot logic.

Risks and test signals: a missing or malformed SBAT file breaks the build or creates incorrect EFI metadata. Test by building with `CONFIG_EFI_SBAT=y`, inspecting the PE section table for `.sbat`, and validating the embedded CSV-like SBAT contents used by shim/firmware tooling.
