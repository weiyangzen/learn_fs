# File Research: sources/cow-pools/nilfs-utils/include/nls.h

Small gettext compatibility wrapper borrowed from util-linux. If NLS is enabled it maps `_()` to `gettext()` and `N_()` to `gettext_noop()` or identity. Otherwise it stubs textdomain/bindtextdomain and returns input strings unchanged.
