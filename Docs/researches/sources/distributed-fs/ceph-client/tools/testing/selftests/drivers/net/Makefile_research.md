# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/Makefile

Purpose: Build/install manifest for driver network kselftests in `drivers/net`.

Important APIs/variables: `CFLAGS += $(KHDR_INCLUDES)`, `TEST_INCLUDES`, `TEST_GEN_FILES`, `TEST_PROGS`, `YNL_GEN_FILES`, `YNL_GENS`, inclusion of `../../lib.mk` and `../../net/ynl.mk`.

Control flow: Make collects Python and shell library includes, builds `napi_id_helper` plus YNL-generated `psp_responder`, and registers multiple Python/shell test programs such as `gro.py`, `hds.py`, `macsec.py`, `napi_threaded.py`, `psp.py`, `queues.py`, and `xdp.py`.

State and persistence: Make outputs generated binaries/YNL artifacts under the kselftest output tree; it does not alter runtime kernel state itself.

Dependencies and integration points: Depends on kselftest core `lib.mk`, network YNL generation, kernel headers, and helper libraries in `net/lib.py` and shell libs.

Risks and test signals: Misdeclared `TEST_PROGS`, `TEST_GEN_FILES`, or includes cause install/run gaps. YNL ordering before `lib.mk` is important for generated Netlink family helpers.
