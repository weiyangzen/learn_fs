# File Research: sources/block-storage/bcache-tools/show.h

This header declares `show_bdevs_detail`, `show_bdevs`, and `detail_single`. The include guard is named `_BCH_MAKE_H`, which is misleading for a show header and could collide conceptually with make-related guards, though the actual `make.h` in this tree has no guard.
