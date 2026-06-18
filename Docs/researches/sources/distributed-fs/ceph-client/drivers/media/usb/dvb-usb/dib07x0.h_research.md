# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/dib07x0.h

Purpose: small shared header for DiB07x0 board GPIO numbering. It gives board files symbolic names for the sparse GPIO line numbers used by the bridge and standardizes input/output direction constants.

Important APIs/types: `enum dib07x0_gpios` maps `GPIO0` through `GPIO10` to hardware line numbers, where several logical GPIO labels skip numeric values. `GPIO_IN` and `GPIO_OUT` encode direction values passed to `dib0700_set_gpio()`.

Control flow: board attach callbacks include this header indirectly through DiB0700 headers and pass these constants into reset, power, LNA, LED, tuner, demod, and analog-component GPIO sequences.

State and persistence: no runtime state. The constants describe stable hardware wiring assumptions used to program persistent GPIO state in the bridge.

Dependencies and integration: integrated with DiB0700 board code and bridge GPIO helpers. It intentionally avoids broader includes beyond its guard.

Risks: a wrong GPIO mapping silently toggles the wrong rail or reset line. The sparse numbering makes integer literals in board files easy to misread, so symbolic use is important.

Test signals: compile DiB0700 board files, then hardware-probe boards whose attach paths exercise GPIO6/GPIO9/GPIO10 resets, GPIO0/GPIO1 LED or LNA control, and tuner reset/sleep lines.
