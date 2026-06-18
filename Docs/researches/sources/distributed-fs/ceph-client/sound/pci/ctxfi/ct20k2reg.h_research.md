# sources/distributed-fs/ceph-client/sound/pci/ctxfi/ct20k2reg.h

Purpose: register-address map for the Creative 20K2 X-Fi hardware backend.

Important APIs and types: defines 20K2 timer, I2C, global control, PLL, SRC, GPIO, virtual memory, transport, audio I/O, and mixer register offsets. The names match the common `struct hw` operation concepts used by ctxfi resource managers.

Control flow and integration: included by the 20K2 backend, not by generic ATC or resource-manager code. It supports chip-specific implementation of the same operation table shape as 20K1.

State and persistence: constants only.

Risks and test signals: as with 20K1, wrong offsets manifest as failed card init or broken routing. Test with 20K2 models across playback, capture, S/PDIF, timer, and suspend/resume paths.
