# sources/distributed-fs/ceph-client/drivers/media/common/siano/Makefile

Purpose: defines Siano common and DVB adaptation composite objects.

Important build artifacts: `smsmdtv.o` includes `smscoreapi.o`, `sms-cards.o`, and `smsendian.o`; `smsdvb.o` includes `smsdvb-main.o`. `smsir.o` is appended when `CONFIG_SMS_SIANO_RC=y`; `smsdvb-debugfs.o` is appended when `CONFIG_SMS_SIANO_DEBUGFS=y`.

Control flow: `obj-$(CONFIG_SMS_SIANO_MDTV)` builds both common core and DVB adaptation modules. Conditional blocks add optional IR/debugfs sources.

State/persistence: no runtime state.

Dependencies/integration: mirrors Siano Kconfig and keeps board metadata in the common core while DVB frontend registration lives in `smsdvb`.

Risks/test signals: optional object combinations must match preprocessor stubs in headers. Build tests should cover RC/debugfs permutations and module/built-in linkage.
