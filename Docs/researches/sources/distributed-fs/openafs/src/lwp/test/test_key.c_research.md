# sources/distributed-fs/openafs/src/lwp/test/test_key.c

Purpose: interactive test for `LWP_WaitForKeystroke`, `LWP_GetResponseKey`, and `LWP_GetLine`.

Important APIs/types/functions: command options include `-nobuf`, `-delay`, `-iters`, `-inter`, and `-line`. `DotWriter` waits on `waitingForAnswer` and prints dots through `PrintDots` while keyboard waits are active. `interTest` beeps every five seconds until a key arrives; `lineTest` waits for a whole line.

Control flow: `main` initializes IOMGR, creates `DotWriter`, chooses interactive mode, signals the dot writer, and calls the keyboard helper under test. In delayed mode, it repeats waits and flushes pending input after a key is available.

State and persistence: process-local flag `waitingForAnswer`, stdin buffering mode, and console output. No persistent data.

Dependencies/integration: includes `lwp.h`; uses IOMGR sleep/select behavior and keyboard wrappers from `waitkey.c`.

Risks and test signals: interactive tests are hard to automate and platform terminal buffering affects behavior. Success is user-visible: dots continue while waiting, timeouts report no data, and entered keys/lines are returned.
