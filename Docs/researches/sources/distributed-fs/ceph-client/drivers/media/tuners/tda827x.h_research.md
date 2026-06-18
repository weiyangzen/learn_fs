# sources/distributed-fs/ceph-client/drivers/media/tuners/tda827x.h

Purpose: public configuration and attach declaration for the TDA827x tuner driver.

Important APIs and types: defines `struct tda827x_config` with optional init/sleep callbacks, TDA8290 LNA configuration, switch I2C address, and an `agcf` callback slot populated by the tuner implementation. Declares `tda827x_attach` or a disabled-driver stub.

Control flow: board code or `tda8290.c` calls `tda827x_attach`; the implementation installs frontend tuner ops and stores the config pointer for later board callbacks and AGC/LNA behavior.

State and persistence: header owns no state. The `agcf` function pointer is mutable output from the driver, so config may be both input and callback handoff state.

Dependencies and integration points: includes I2C, DVB frontend, and `tda8290.h` for LNA enum values. This tight coupling reflects common TDA829x plus TDA827x combo hardware.

Risks: the config pointer must remain valid for the attachment lifetime. The disabled stub returns `NULL`. `agcf` as an output field can surprise callers expecting config to be immutable.

Test signals: build with TDA827x enabled/disabled, attach through both board code and TDA8290 discovery, callback invocation for init/sleep/AGC, and LNA switch address verification.
