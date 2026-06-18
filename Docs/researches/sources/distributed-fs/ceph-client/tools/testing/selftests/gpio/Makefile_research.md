<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/gpio/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/gpio/Makefile

## Purpose
This Makefile builds and registers GPIO selftests for mockup, simulator, aggregator, and character-device UAF coverage.

## Important APIs, Types, And Functions
It sets `TEST_PROGS := gpio-mockup.sh gpio-sim.sh gpio-aggregator.sh gpio-cdev-uaf.sh`, `TEST_FILES := gpio-mockup-sysfs.sh`, `TEST_GEN_PROGS_EXTENDED := gpio-mockup-cdev gpio-chip-info gpio-line-name gpio-cdev-uaf`, and `CFLAGS += -O2 -g -Wall $(KHDR_INCLUDES)`.

## Control Flow
kselftest builds helper binaries, installs shell scripts, and runs the four main GPIO test scripts.

## State And Persistence
Build artifacts are generated; runtime module/configfs/debugfs state is owned by scripts.

## Dependencies And Integration Points
It integrates with GPIOLIB, GPIO cdev, `gpio-mockup`, `gpio-sim`, and `gpio-aggregator` modules.

## Risks
Missing helper binaries break shell scripts that query chip info or exercise cdev line requests.

## Test Signals
Successful helper builds and PASS messages from mockup, sim, aggregator, and UAF scripts validate the Makefile.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/gpio/Makefile -->
