<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/ideapad-laptop.h -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/ideapad-laptop.h

Purpose: public internal header for the Lenovo IdeaPad notifier interface used by companion Lenovo platform drivers, especially Yoga Mode Control integration.

Important APIs/types: `enum ideapad_laptop_notifier_actions` currently defines `IDEAPAD_LAPTOP_YMC_EVENT`. The header declares `ideapad_laptop_register_notifier()`, `ideapad_laptop_unregister_notifier()`, and `ideapad_laptop_call_notifier()`.

Control flow: no implementation here. `ideapad-laptop.c` backs the declarations with a blocking notifier chain and exports the functions in namespace `IDEAPAD_LAPTOP`.

State/persistence: no header state. Consumers register notifier blocks; the implementation stores them in the blocking notifier chain.

Dependencies/integration: depends only on `linux/notifier.h`. It decouples companion modules from the full IdeaPad private structure while allowing YMC events to trigger IdeaPad EC workarounds.

Risks: the action enum is currently narrow; expanding it requires coordinated implementation handling. Consumers must obey notifier-block lifetime rules and unregister before unload.

Test signals: companion modules should compile by including this header and importing namespace `IDEAPAD_LAPTOP`; notifier registration should receive `IDEAPAD_LAPTOP_YMC_EVENT` when `ideapad_laptop_call_notifier()` is invoked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/ideapad-laptop.h -->
