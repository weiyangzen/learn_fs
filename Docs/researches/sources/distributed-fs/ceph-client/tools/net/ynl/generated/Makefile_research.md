# sources/distributed-fs/ceph-client/tools/net/ynl/generated/Makefile

Purpose: Generates, compiles, archives, documents, cleans, regenerates, and installs user-space C bindings and RST documentation from YAML netlink specs.

Important targets and variables: `TOOL` points to `../pyynl/ynl_gen_c.py`, `TOOL_RST` to `../pyynl/ynl_gen_rst.py`, and `SPECS_DIR` to `Documentation/netlink/specs`. `GENS` derives from all YAML specs except unsupported `conntrack` and `nftables`; generated outputs include `%-user.h`, `%-user.c`, `%-user.o`, `protos.a`, and `%.rst`. `YNL_GEN_ARG_ethtool` supplies ethtool-specific generation arguments.

Control flow: Pattern rules generate headers and sources from specs, compile source objects with `$(COMPILE.c)`, archive objects into `protos.a`, and generate RST docs. `regen` delegates to `../ynl-regen.sh`. Install targets separately install headers, RSTs, and spec YAML files, with `install` aggregating them.

Dependencies and integration: Includes `../Makefile.deps`, depends on UAPI headers via `-idirafter $(UAPI_PATH)`, and is consumed by the top-level YNL Makefile when building `libynl.a`.

State and persistence: Produces generated `.c`, `.h`, `.o`, `.a`, and `.rst` files, plus installed headers/docs/specs. `distclean` removes generated artifacts while `clean` only removes objects.

Risks: The duplicate `SPECS_PATHS` assignment is harmless but easy to drift. Unsupported specs are hard-coded. `install-specs` copies `Documentation/netlink/*.yaml` as well as specs, so path mistakes affect package contents. Generated code quality depends on the Python generators and current spec schema.

Test signals: Build all generated artifacts, verify ethtool exclusion args, compile with `DEBUG=1`, run `make regen`, run `distclean` followed by `all`, and test staged installs of headers, RSTs, and specs.
