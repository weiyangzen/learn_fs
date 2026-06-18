# sources/distributed-fs/ceph-client/drivers/gpu/nova-core/gsp/sequencer.rs

Purpose: executes the pre-Hopper GSP CPU sequencer command stream received from firmware during boot. It converts raw sequencer buffer bytes into typed operations over BAR0 registers and Falcon cores.

Important APIs and types: `GspSequence` implements `MessageFromGsp` for `fw::MsgFunction::GspRunCpuSequencer`. `GspSeqCmd` represents register write/modify/poll/store, delay, core reset/start/wait/resume. `GspSeqIter` parses command bytes. `GspSequencer::run()` receives the firmware message and executes commands with `GspSequencerParams`.

Control flow: `run()` loops on `cmdq.receive_msg`, ignoring `ERANGE`, then builds a sequencer and iterates command data. Each parsed command dispatches to register access or Falcon control. `CoreResume` resets GSP, writes libOS DMA handle mailboxes, starts SEC2, waits for GSP reload completion, checks SEC2 errors, writes bootloader version, and verifies RISC-V active.

State and persistence: transient state includes command data, current parse offset, command count, libOS DMA handle, and bootloader version. Persistent hardware state is changed through BAR0 registers and Falcon core state.

Dependencies and integration: depends on `Cmdq`, firmware payload wrappers, `Bar0`, `Falcon<Gsp>`, `Falcon<Sec2>`, polling/delay APIs, and `SBufferIter` for command-buffer collection.

Risks: command parsing zero-pads tail bytes and stops silently on parse errors inside the iterator, so malformed firmware streams need careful logging. Hardware sequencing order is critical; timeout defaults, mailbox values, and active-core checks are boot blockers.

Test signals: no unit tests. Signals are GSP boot success, sequencer debug logs, register-poll timeout behavior, SEC2 mailbox error reporting, and hardware bring-up coverage.
