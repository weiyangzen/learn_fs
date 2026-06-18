## sources/distributed-fs/openafs/src/kauth/test/Makefile.in

Purpose: this makefile builds kauth test utilities and defines the historical `runtest` integration sequence.

Important targets: `all test tests` build only `multiklog`, and the comment says the only tests known to work are `multiklog` and Tcl scripts. Additional explicit targets build `test_date`, `test_badtix`, `decode_ticket`, `test_interim_ktc`, `test_rxkad_free`, `test_getticket`, and `background`. `runtest` builds selected helpers, runs `test_interim_ktc`, `test_kaserver`, and two `test_rxkad_free` modes.

Dependencies and integration points: links against LWP, DES, rxkad, auth, cmd, ubik, prot, sys, rx, com_err, kauth, and afsutil. Test configuration variables require real usernames, passwords, Vice IDs, optional remote-cell credentials, and running KA/PT/cache-manager services.

State and persistence: test scripts create files/processes under `/tmp`, start background kaserver instances, and manipulate local token state and test directories.

Risks: defaults such as `TESTERNAME=xxx` and `TESTERPASSWORD=xxx` make `runtest` unsuitable without explicit local configuration. Several test programs are not part of default `all`, and the file itself warns that most C tests may not be known-good.

Test signals: the file is the primary signal map for kauth tests: `multiklog` is the default build smoke test; `runtest` is the broader integration lane for token cache, kaserver, ticket, and rxkad cleanup behavior.
