# sources/distributed-fs/ceph-client/include/uapi/linux/gameport.h

This UAPI header defines constants for the legacy gameport input subsystem. It names gameport operating modes and vendor IDs used by joystick/gameport drivers and userspace identification tools.

Important exports are modes `GAMEPORT_MODE_DISABLED`, `GAMEPORT_MODE_RAW`, and `GAMEPORT_MODE_COOKED`, plus vendor IDs for Analog, Mad Catz, Logitech, Creative, Genius, InterAct, Microsoft, Thrustmaster, Gravis, and Guillemot.

Control flow is indirect through gameport/input drivers: drivers identify or switch gameport mode and expose input devices; userspace mostly observes the resulting input events or metadata. The header stores no state. Runtime state is in the gameport driver, hardware port mode, attached device protocol, and input subsystem device registration.

Dependencies are the legacy gameport core and input subsystem. Integration points include old joystick drivers, input device enumeration, and compatibility with historical hardware.

Risks include stale vendor ID coverage, limited hardware availability, raw/cooked mode mismatch, and keeping obsolete constants stable for old userspace. Test signals include build coverage for gameport drivers, input enumeration tests on supported hardware or emulators, and header compatibility checks.
