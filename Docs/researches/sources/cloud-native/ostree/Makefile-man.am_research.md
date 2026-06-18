<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/Makefile-man.am -->
## sources/cloud-native/ostree/Makefile-man.am

### Purpose
This fragment generates and installs OSTree man pages and optional HTML manpage output from DocBook XML sources.

### APIs, Types, and Control Flow
Under `ENABLE_MAN`, it defines `man1`, `man5`, and `man8` file lists, conditionally adding FUSE and GPGME pages. It maps them to automake `*_MANS`, defines `manhtml_files`, adds a convenience `manhtml` target under `ENABLE_MAN_HTML`, and provides XSLT rules for `.1`, `.5`, `.8`, and `man/html/*.html` generation using `xsltproc --nonet`.

### State, Dependencies, and Integration
Generated man and HTML files are added to `CLEANFILES`; XML sources and the HTML stylesheet are distributed. It integrates with docs workflow and top-level `make manhtml`.

### Risks and Test Signals
The comment notes new man pages must also be referenced in index XML. Network use is disabled through `--nonet`, so local stylesheets/catalogs must be available. Test signal is successful `make manhtml`, `make dist`, and docs workflow.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/Makefile-man.am -->
